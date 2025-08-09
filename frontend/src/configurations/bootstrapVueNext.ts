/**
 * Configuration file for BootstrapVueNext.
 * Refer to the documentation for more details:
 * https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/configurations/global-options.html
 */

export default {
  // Future configuration options will be added here
  components: {
    // Configurations for using our link-component as default
    BLink: {
      routerComponentName: "BaseLink",
    },
    BDropdownItem: {
      routerComponentName: "BaseLink",
    },
    BButton: {
      routerComponentName: "BaseLink",
    },
  },
};
