 <template>
  <span :class="[iconClass, noPropsClass, customClass]">
    {{ name }}
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  name: { type: String, required: true },
  variant: {
    type: String,
    default: "filled",
    validator: v =>
      ["filled", "outlined", "round", "sharp", "two-tone"].includes(v),
  },
  size: { type: String, default: "18px" },
  customClass: { type: String, default: "" }, 
});

const noPropsClass = computed(() => {
  return props.customClass ? "" : "no-props";
});

const iconClass = computed(() => {
  switch (props.variant) {
    case "outlined":
      return "material-icons-outlined";
    case "round":
      return "material-icons-round";
    case "sharp":
      return "material-icons-sharp";
    case "two-tone":
      return "material-icons-two-tone";
    default:
      return "material-icons";
  }
});
</script>

<style scoped>
span {
  font-size: v-bind(size);
  line-height: 1;
  vertical-align: middle;
}
</style>
