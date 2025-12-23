/**
 * Vue directive for scroll-based triggers
 * Executes a callback when element is scrolled to the bottom
 * @module directives/when-scrolled
 */

/**
 * When-scrolled directive
 * Usage: v-when-scrolled="callback"
 * Calls the callback function when the element is scrolled to the bottom
 * @example
 * <div v-when-scrolled="loadMore" style="height: 300px; overflow-y: auto">
 *   <!-- content -->
 * </div>
 */
export default {
    bind(el, binding) {
        const handleScroll = () => {
            // Check if scrolled to bottom
            if (el.scrollTop + el.offsetHeight >= el.scrollHeight) {
                // Execute the bound function
                if (typeof binding.value === 'function') {
                    binding.value();
                }
            }
        };

        // Store the handler on the element for cleanup
        el._whenScrolledHandler = handleScroll;
        
        // Attach scroll listener
        el.addEventListener('scroll', handleScroll);
    },

    unbind(el) {
        // Clean up event listener
        if (el._whenScrolledHandler) {
            el.removeEventListener('scroll', el._whenScrolledHandler);
            delete el._whenScrolledHandler;
        }
    }
};

/**
 * Install the directive in a Vue instance
 * @param {Vue} Vue - Vue constructor
 * @example
 * import whenScrolled from './directives/when-scrolled';
 * Vue.directive('when-scrolled', whenScrolled);
 */
export function install(Vue) {
    Vue.directive('when-scrolled', {
        bind(el, binding) {
            const handleScroll = () => {
                if (el.scrollTop + el.offsetHeight >= el.scrollHeight) {
                    if (typeof binding.value === 'function') {
                        binding.value();
                    }
                }
            };

            el._whenScrolledHandler = handleScroll;
            el.addEventListener('scroll', handleScroll);
        },

        unbind(el) {
            if (el._whenScrolledHandler) {
                el.removeEventListener('scroll', el._whenScrolledHandler);
                delete el._whenScrolledHandler;
            }
        }
    });
}
