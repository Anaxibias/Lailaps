import m from "mithril";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import './styles/style.css';
import Layout from "./components/Layout.js";

const App = {
  view: (vnode) => m(Layout, vnode.children)
};

m.mount(document.getElementById("app"), App);