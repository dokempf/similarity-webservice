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
        <a href={item.repo_url} target="_blank">
          <img src={item.image_url} alt="Image Link Broken" class={twMerge(imgClass, $$props.classImg)} />
        </a>
        Similarity Score: {(item.score * 100).toFixed(2)}%
      </div>
    </slot>
  {:else}
    <slot item={items[0]} />
  {/each}
</div>
