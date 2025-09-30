// src/plugins/primevue.js
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import 'primeicons/primeicons.css'

import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import Popover from 'primevue/popover'
import Menu from 'primevue/menu'
import Avatar from 'primevue/avatar'
import Password from 'primevue/password'
import Dialog from 'primevue/dialog'
import Message from 'primevue/message'
import Tooltip from 'primevue/tooltip'
import Card from 'primevue/card'
import Dropdown from 'primevue/dropdown'
import InputMask from 'primevue/inputmask'
import InlineMessage from 'primevue/inlinemessage'
import KeyFilter from 'primevue/keyfilter'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import MultiSelect from 'primevue/multiselect'
import DatePicker from 'primevue/datepicker'
import InputNumber from 'primevue/inputnumber'
import Slider from 'primevue/slider'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'

let installed = false
export default {
  install(app) {
    if (installed) return; 
    installed = true

    app.component('InputText', InputText)
    app.component('Button', Button)
    app.component('Badge', Badge)
    app.component('Popover', Popover)
    app.component('Menu', Menu)
    app.component('Avatar', Avatar)
    app.component('Password', Password)
    app.component('Dialog', Dialog)
    app.component('Message', Message)
    app.component('Tooltip', Tooltip)
    app.component('Card', Card)
    app.component('Dropdown', Dropdown)
    app.component('InputMask', InputMask)
    app.component('InlineMessage', InlineMessage)
    app.directive('keyfilter', KeyFilter)
    app.component('InputGroup', InputGroup)
    app.component('InputGroupAddon', InputGroupAddon)
    app.component('DataTable', DataTable)
    app.component('Column', Column)
    app.component('Tag', Tag)
    app.component('ProgressBar', ProgressBar)
    app.component('MultiSelect', MultiSelect)
    app.component('DatePicker', DatePicker)
    app.component('InputNumber', InputNumber)
    app.component('Slider', Slider)
    app.component('IconField', IconField)
    app.component('InputIcon', InputIcon)
    app.component('Select', Select)
    app.component('Checkbox', Checkbox)
  }
}
