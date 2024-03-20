<script lang="ts">
  import { twMerge } from 'tailwind-merge';

  export let items = [];
  export let imgClass: string = 'h-auto max-w-full rounded-lg';

  $: divClass = twMerge('grid', $$props.class);

  function init(node: HTMLElement) {
    if (getComputedStyle(node).gap === 'normal') node.style.gap = 'inherit';
  }
</script>

<div {...$$restProps} class={divClass} use:init>
  {#each items as item}
    <slot {item}>
      <div>
        <a href={item.href} target="_blank">
          <img src={item.src} alt={item.alt} class={twMerge(imgClass, $$props.classImg)} />
        </a>
      </div>
    </slot>
  {:else}
    <slot item={items[0]} />
  {/each}
</div>
