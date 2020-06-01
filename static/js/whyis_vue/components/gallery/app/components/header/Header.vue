<template>
    <md-app-toolbar class="md-primary md-large nav-bg">
        <div class="md-toolbar-row">
          <md-button class="md-icon-button" @click="toggle">
            <md-icon>menu</md-icon>
          </md-button>
          <span class="md-title nav-title" v-if="otherArgs != null && authenticated">Visualization Gallery - {{ otherArgs }}</span>
          <span class="md-title nav-title" v-else>Visualization Gallery</span>
          <div class="md-toolbar-section-end">
            <md-button class="md-icon-button" v-if="authenticated">
              <md-avatar>
                <img src="https://vuematerial.io/assets/examples/avatar.png" alt="Avatar">
              </md-avatar>
            </md-button>
            <span class="md-subheading utility-cursor" v-else @click="login">Login</span>
            
          </div>
        </div>
    </md-app-toolbar>
</template>

<style scoped lang="scss" src="../../static/css/main.scss"></style>

<script>
import { eventCourier as ec } from '../../store';
export default {
  name: 'Header',
  props:{
    authenticated: {
      type: Boolean
    }
  },
  data(){
    return {
      profileImage: null,
      otherArgs: null
    }
  },
  methods:{
    toggle(){
      return ec.toggleNav()
    },
    login(){
      return ec.getAuth()
    }
  },
  created(){
      ec
      .$on("route-args", (data) => {
        return this.otherArgs = data
      })
  }
}
</script>