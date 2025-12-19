<template>
    <div class="search-page">
        <div class="container-fluid py-4">
            <!-- Search Bar -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="search-bar-container">
                        <div class="input-group input-group-lg">
                            <input
                                ref="searchInput"
                                v-model="searchQuery"
                                type="text"
                                class="form-control"
                                placeholder="Search knowledge base..."
                                @keydown.enter="performSearch"
                            />
                            <button 
                                class="btn btn-primary" 
                                type="button"
                                @click="performSearch"
                            >
                                <i class="bi bi-search"></i> Search
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <spinner :loading="loading" text='Searching...' v-if="loading"/>

            <!-- Results Container -->
            <div v-else class="row">
                <!-- Main Results Column -->
                <div :class="'col-12'">
                    <div v-if="searchPerformed && searchQuery" class="results-info mb-3">
                        <span v-if="results.length === 0">No results found for "{{ searchQuery }}"</span>
                        <span v-else-if="results.length === 1">1 result for "{{ searchQuery }}"</span>
                        <span v-else>{{ totalResults }} results for "{{ searchQuery }}"</span>
                    </div>

                    <!-- Results List -->
                    <div v-if="results.length > 0" class="results-list">
                        <div 
                            v-for="(result, index) in displayedResults" 
                            :key="result.identifier || index"
                            class="result-item card mb-3"
                        >
                            <div class="card-body">
                                <h5 class="card-title">
                                    <a :href="getViewUrl(result.identifier)" class="text-decoration-none">
                                        {{ result.label || 'Untitled' }}
                                    </a>
                                </h5>
                                <div v-if="result.type && result.type.length > 0" class="text-muted small mb-2">
                                    <span v-for="(type, idx) in result.type" :key="idx">
                                        {{ type.label }}<span v-if="idx < result.type.length - 1">, </span>
                                    </span>
                                </div>
                                <blockquote v-if="result.text" class="card-text blockquote"
				   v-html="highlightQuery(result.text, searchQuery)">
                                </blockquote>
                                <p v-if="result.description" class="card-text">
                                    {{ truncateDescription(result.description) }}
                                </p>
                                <div class="text-muted small">
                                    <a :href="getViewUrl(result.identifier)" class="text-decoration-none">
                                        {{ result.identifier }}
                                    </a>
                                </div>
                            </div>
                        </div>

                        <!-- Load More Indicator -->
                        <div 
                            v-if="hasMore" 
                            ref="loadMoreTrigger" 
                            class="text-center py-3"
                        >
                            <div v-if="loadingMore" class="spinner-border" role="status">
                                <span class="visually-hidden">Loading more...</span>
                            </div>
                            <div v-else class="text-muted">
                                Scroll for more results
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<style scoped>
.search-page {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.search-bar-container {
    max-width: 800px;
    margin: 0 auto;
}

.results-info {
    color: #6c757d;
    font-size: 0.9rem;
}

.result-item {
    transition: box-shadow 0.2s ease;
}

.result-item:hover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.result-item .card-title a {
    color: #1a0dab;
}

.result-item .card-title a:hover {
    text-decoration: underline !important;
}
</style>

<script>
import Vue from 'vue';
import axios from 'axios';

export default Vue.component('search-page', {
    data() {
        return {
            searchQuery: '',
            results: [],
            displayedResults: [],
            loading: false,
            loadingMore: false,
            searchPerformed: false,
            page: 0,
            pageSize: 10,
            totalResults: 0,
            observer: null,
            topResultAttributes: null
        };
    },
    computed: {
        hasMore() {
            return this.displayedResults.length < this.results.length;
        },
        hasTopResult() {
            return false; //this.topResultAttributes !== null && this.results.length > 0;
        }
    },
    methods: {
        async performSearch() {
            if (!this.searchQuery || this.searchQuery.trim().length < 3) {
                return;
            }

            this.loading = true;
            this.searchPerformed = true;
            this.results = [];
            this.displayedResults = [];
            this.page = 0;
            this.topResultAttributes = null;

            try {
                const response = await axios.get('/about', {
                    params: { 
                        view: 'search_data', 
                        query: this.searchQuery 
                    },
                    responseType: 'json'
                });

                if (response.data && Array.isArray(response.data)) {
                    this.results = response.data;
                    this.totalResults = this.results.length;
                    this.loadNextPage();

                    // Load top result details if available
                    if (this.results.length > 0 && this.results[0].identifier) {
                        await this.loadTopResult(this.results[0].identifier);
                    }
                }
            } catch (error) {
                console.error('Error performing search:', error);
                this.results = [];
            } finally {
                this.loading = false;
            }
        },

        async loadTopResult(uri) {
            try {
                const response = await axios.get('/about', {
                    params: { 
                        view: 'summary', 
                        uri: uri 
                    },
                    responseType: 'json'
                });

                if (response.data) {
                    this.topResultAttributes = response.data;
                }
            } catch (error) {
                console.error('Error loading top result:', error);
            }
        },

        loadNextPage() {
            const start = this.page * this.pageSize;
            const end = start + this.pageSize;
            const newResults = this.results.slice(start, end);
            
            this.displayedResults = [...this.displayedResults, ...newResults];
            this.page++;

            this.$nextTick(() => {
                this.setupIntersectionObserver();
            });
        },

        setupIntersectionObserver() {
            if (this.observer) {
                this.observer.disconnect();
            }

            if (!this.hasMore || !this.$refs.loadMoreTrigger) {
                return;
            }

            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && this.hasMore && !this.loadingMore) {
                        this.loadingMore = true;
                        // Load next page (synchronous operation on already-fetched data)
                        this.loadNextPage();
                        // Clear loading flag after DOM updates
                        this.$nextTick(() => {
                            this.loadingMore = false;
                        });
                    }
                });
            }, {
                threshold: 0.1
            });

            this.observer.observe(this.$refs.loadMoreTrigger);
        },

        getViewUrl(uri) {
            if (!uri) return '#';
            return '/about?view=view&uri=' + encodeURIComponent(uri);
        },

        highlightQuery(text, query) {
  	    if (!text || !query) return text;

            // Split query into individual words
            const words = query.split(/\s+/).filter(Boolean);

            // Escape regex special characters
            const escapedWords = words.map(word =>
                  word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
            );

            // Create a regex that matches any of the words (whole words, case-insensitive)
            const regex = new RegExp(`\\b(${escapedWords.join("|")})\\b`, "gi");

            // Wrap matches in <mark>
            return text.replace(regex, "<mark>$1</mark>");
        },

        trimToMarked(markedText, maxWords) {
            if (!markedText || maxWords <= 0) return "";

            // Split into HTML tags and text
            const tokens = markedText.match(/(<[^>]+>|[^<]+)/g) || [];

            // Build a list of visible words with their token indices
            const words = [];
            tokens.forEach((token, tokenIndex) => {
                if (token.startsWith("<")) return;

                const parts = token.split(/\b/);
                parts.forEach((part, partIndex) => {
                    if (/\w+/.test(part)) {
                        words.push({
                            word: part,
                            tokenIndex,
                            partIndex
                        });
                    }
                });
            });

            if (words.length === 0) return markedText;

            // Find word indices that are inside <mark> tags
            const markedWordIndexes = [];
            let insideMark = false;

            tokens.forEach((token, tokenIndex) => {
                if (token.match(/<mark\b/i)) insideMark = true;
                if (!token.startsWith("<") && insideMark) {
                    const wordMatches = token.match(/\b\w+\b/g) || [];
                    wordMatches.forEach(() => {
                        markedWordIndexes.push(markedWordIndexes.length);
                    });
                }
                if (token.match(/<\/mark>/i)) insideMark = false;
            });

            if (markedWordIndexes.length === 0) {
                return words.length > maxWords
                       ? words.slice(0, maxWords).map(w => w.word).join(" ") + "…"
                       : markedText;
            }

            const first = markedWordIndexes[0];
            const last = markedWordIndexes[markedWordIndexes.length - 1];

            const markedCount = last - first + 1;
            const remaining = Math.max(0, maxWords - markedCount);
            const before = Math.floor(remaining / 2);
            const after = remaining - before;

            const startWord = Math.max(0, first - before);
            const endWord = Math.min(words.length - 1, last + after);

            // Determine which tokens to keep
            const keepTokenIndexes = new Set();
            for (let i = startWord; i <= endWord; i++) {
                keepTokenIndexes.add(words[i].tokenIndex);
            }

            let result = "";
            let openMarks = 0;

            tokens.forEach((token, i) => {
                if (!keepTokenIndexes.has(i) && !token.match(/<\/?mark/i)) return;

                if (token.match(/<mark\b/i)) openMarks++;
                if (token.match(/<\/mark>/i)) openMarks--;

                result += token;
            });

            // Close any unclosed <mark> tags
            while (openMarks > 0) {
                result += "</mark>";
                openMarks--;
            }

            if (startWord > 0) result = "…" + result;
            if (endWord < words.length - 1) result += "…";

            return result;
        },

        truncateDescription(description) {
            if (!description) return '';
            if (typeof description === 'string') {
                return description.length > 200 
                    ? description.substring(0, 200) + '...' 
                    : description;
            }
            return '';
        }
    },

    mounted() {
        // Get query from URL if present
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('query');
        
        if (query) {
            this.searchQuery = query;
            this.performSearch();
        }

        // Focus search input
        this.$nextTick(() => {
            if (this.$refs.searchInput) {
                this.$refs.searchInput.focus();
            }
        });
    },

    beforeDestroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
});
</script>
