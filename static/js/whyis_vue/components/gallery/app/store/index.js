import Vue from 'vue';

const state = {
    appRoutes: {
        currentPage: null,
        pageHistory: [],
        pageArgs: []
    }
}

const eventCourier = new Vue({
    data:{
        appState: [],
        navOpen: false,
        authenticated: {
            status: false,
            role: null
        },
        darkThemeEnabled: false
    },
    watch:{
        appState(newVal, oldVal){
            if(newVal !== oldVal){
                this.getState();
            }
        },
        authenticated(newVal){
            if(newVal){
                localStorage.setItem('authenticated', JSON.stringify(this.authenticated));
                return this.$emit('isauthenticated', this.authenticated);
            }
        }
    },
    methods:{
        addItem(data){
            return this.appState = data
        },
        updateStateItem(data){
            return this.appState = [...this.appState,...data]
        },
        deleteStateItem(item){
            this.appState.splice(this.appState.findIndex(el => el == item),1)
        },
        getState(){
            return this.$emit('appstate', this.appState);
        },

        /** Navigation Handler Method */
        toggleNav(){
            this.navOpen = !this.navOpen;
            return this.$emit('togglenavigation', this.navOpen);
        },
        
        /** Authentication Handler Methods */
        getAuth(args) {
            if(args){
                this.authenticated = args;
                return this.$emit('isauthenticated', this.authenticated);
            }
            return this.authenticated = JSON.parse(localStorage.getItem('authenticated'));
        },
        exitApp(){
            this.authenticated = {status: false, role: null}
            localStorage.setItem('authenticated', JSON.stringify(this.authenticated));
            return this.$emit('isauthenticated', this.authenticated);
        }, 
        authenticate(args) {
            return this.getAuth({status: true, role: "user"})
        },

        /** Change themes */
        changeTheme(){
            const elements = ["utility-content__result", "utility-color", "utility-float-icon", "utility-gridborder", "utility-navadjust", "utility-bg", "utility-bg_border"]
            const darkTheme = ["utility-content__result-dark", "utility-color-dark", "utility-float-icon-dark", "utility-gridborder-dark", "utility-navadjust-dark", "utility-bg-dark", "utility-bg_border-dark"]
            const body = document.getElementsByTagName("BODY")[0];
            this.darkThemeEnabled == true ? body.setAttribute("style", "background:#ffffff !important;") : body.setAttribute("style", "background:#000000 !important;");

            elements.forEach((el, index) => {
                if(this.darkThemeEnabled == false){
                    const current = document.querySelectorAll("."+el)
                    if(current.length >= 1){
                        current.forEach(e => {
                            e.classList.add(darkTheme[index])
                            e.classList.remove(el)
                        })
                    }
                } else {
                    const current = document.querySelectorAll("."+darkTheme[index])
                    if(current.length >= 1){
                        current.forEach(e => {
                            e.classList.add(el)
                            e.classList.remove(darkTheme[index])
                        })
                    }
                }
            })
            return this.darkThemeEnabled = !this.darkThemeEnabled
        }
    },
    created(){
        return this.getState()
    }
})

/** Outside Navigation Click Handler */
document.addEventListener("click", () => {
    eventCourier.$data.navOpen = false;
});

export {
    state,
    eventCourier
}