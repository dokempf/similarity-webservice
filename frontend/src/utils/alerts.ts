import { writable } from 'svelte/store'
import type { Writable } from 'svelte/store'

function createAlertsStore (): object {
  const { subscribe, update }: Writable< Array<{ msg: string, color: 'dark' | 'gray' | 'red' | 'yellow' | 'green' | 'orange' }> > = writable([])

  return {
    subscribe,
    add: function (msg: string, color: 'dark' | 'gray' | 'red' | 'yellow' | 'green' | 'orange' = 'dark'): void {
      update((alerts) => alerts.concat({ msg: msg, color: color }))
    }
  }
}

export const alerts = createAlertsStore()
