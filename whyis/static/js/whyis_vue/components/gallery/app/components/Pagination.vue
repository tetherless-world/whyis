<template>
    <div class="viz-pagination-container">
        <span>Page {{ currPage }} of {{ tpages }}</span>
        <div class="viz-pagination">
            <a href="#" @click.prevent="navigate('home')" class="viz-u-display__desktop">Home</a>
            <a href="#" @click.prevent="navigate('prev')">Prev</a>
            <a href="#" @click.prevent="navigate('next')">Next</a>
            <a href="#" @click.prevent="navigate('end')" class="viz-u-display__desktop">End</a>
        </div>
    </div>
</template>
<style lang="scss" src="../../../../assets/css/main.scss"></style>
<script>
    import EventServices from '../../../../modules/events/event-services'
    export default {
        name: "pagination",
        props: ['cpage', 'tpages', 'from'],
        data(){
            return {
                currPage: EventServices.currentPage
            }
        },
        methods: {
            navigate(arg){
                switch(arg){
                    case 'home':
                        EventServices.currentPage == 1 ? false : EventServices.currentPage = 1;
                        break;
                    case 'prev':
                        EventServices.currentPage >= 2 ? EventServices.currentPage = EventServices.currentPage - 1 : false;
                        break;
                    case 'next':
                        EventServices.currentPage < this.tpages ? EventServices.currentPage = EventServices.currentPage + 1 : false;
                        break;
                    case 'end':
                        EventServices.currentPage == this.tpages ? false : EventServices.currentPage = this.tpages;
                        break;
                    default:
                        break;
                }
                this.currPage = EventServices.currentPage;
                if(this.from && this.from == 'settingspage'){
                    return EventServices.$emit("settingpagination", EventServices.settingsPage)
                } else {
                    return EventServices.$emit("chartpagination", EventServices.currentPage)
                }
            }
        }
    }
</script>