import m from "mithril";
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import "bootstrap-icons/font/bootstrap-icons.css";
import './styles/style.css';
import Layout from "./components/Layout.js";
import Dashboard from "./pages/Dashboard.js";

m.route(document.body, "/dashboard", {
    "/dashboard": {
        render: () => {
            return m(Layout, m(Dashboard));
        }
    }
});