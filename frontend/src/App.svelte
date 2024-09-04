<script lang="ts">
  import { Navbar, NavBrand, NavHamburger, NavUl, NavLi } from "flowbite-svelte";
  import { GithubSolid, InfoCircleSolid } from "flowbite-svelte-icons";
  import { alerts } from "./utils/alerts";

  import Router from "svelte-spa-router";

  import About from "./routes/About.svelte";
  import Collection from "./routes/Collection.svelte";
  import Search from "./routes/Search.svelte";
  import NotFound from "./routes/Notfound.svelte";
  import TimedAlert from "./components/TimedAlert.svelte";

  export const routes = {
    "/": Search,
    "/collection": Collection,
    "/search": Search,
    "/about": About,
    "*": NotFound
  };

</script>

<!--fixed: position is relative to browser window, w-full: full width, z-20: 3d pos (closer)-->
<header class="fixed w-full z-20 top-0 start-0">
  <!--px/py: padding in x/y direction (one small screens: larger x padding for touch)-->
  <Navbar class="px-2 sm:px-4 py-1.5 bg-slate-300 dark:bg-slate-900">
    <NavHamburger />
    <NavBrand href="#/">
      <!--TODO add icon like this: <img src="/images/flowbite-svelte-icon-logo.svg" class="me-3 h-6 sm:h-9" alt="Flowbite Logo" />-->
      <!-- self-center: x/&y centering for flex item, whitespace-nowrap: text should not wrap, text-xl/font-semibold: font size/type-->
      <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">Similarity Search</span>
    </NavBrand>
    <NavUl>
      <NavLi href="#/" active={true}>Similarity Search</NavLi>
      <NavLi href="#/collection">Collection Management</NavLi>
      <NavLi href="#/about">About</NavLi>
      <NavLi href="https://github.com/ssciwr/similarity-webservice"><GithubSolid class="mx-auto"/></NavLi>
    </NavUl>
  </Navbar>

  {#each $alerts as alert}
    <TimedAlert color={alert.color} dismissable class="m-2">
      <InfoCircleSolid slot="icon" class="w-4 h-4" />
      {alert.msg}
    </TimedAlert>
  {/each}
</header>

<main class="w-screen min-h-dvh bg-slate-200 dark:bg-slate-950">
  <!--overflow-auto: adds scroll bar only if overflow happens (under navbar), w-full: width to parent width, min-h-full: height to parent width (always), px-4: padding to left/right of screen, mx-auto: center horizontally, mt-16: margin to top (this will be "under" navbar)-->
  <div class="flex flex-col overflow-auto w-full min-h-full px-4 mt-16 items-center">
    <Router {routes}/>
  </div>
</main>
