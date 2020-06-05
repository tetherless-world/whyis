
import { eventCourier as ec, state } from '../store'
export const router = {
    methods: {
        changeRoute(page, args){
            state.appRoutes.pageHistory.unshift(page);
            state.appRoutes.currentPage = page
            if(args){
                ec.$emit('route-args', args)
                state.appRoutes.pageArgs.unshift(args);
            } else {
                state.appRoutes.pageArgs.unshift(null);
            }
            return ec.$emit('route-changed', page);
        },
        goBack(){
            if(state.appRoutes.pageHistory.length > 1){
                state.appRoutes.pageHistory.splice(0,1)
                state.appRoutes.currentPage = state.appRoutes.pageHistory[0]

                /** Page Arguement Handler */
                if(state.appRoutes.pageArgs.length > 1){
                    state.appRoutes.pageArgs.splice(0,1)
                    if(state.appRoutes.pageArgs.length >=1){
                        ec.$emit('route-args', state.appRoutes.pageArgs[0])
                    }
                }
                return ec.$emit('route-changed', state.appRoutes.currentPage);
            }
        }
    }
}