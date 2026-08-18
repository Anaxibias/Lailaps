import m from "mithril";
import logoImg from '../images/lailaps-logo-full.png';

const isAuthenticated = true; // Replace with your actual authentication logic
const currentUser = { name: "John Doe" }; // Replace with your actual user data

const Layout = {
    view: (vnode) => {
        return m(".navbar.navbar-dark.py-1", [
            m(".container-fluid", [
                m(".d-flex.flex-column.align-items-center", [
                    m("a.ps-4.pt-2.mt-2.d-flex.align-items-center.mb-0.pb-0.text-decoration-none", {
                        href: "#!/dashboard", 
                        style: {"font-family": "'Kufam', sans-serif", "font-size": "3rem", "color": "#e8e8e8"}
                    }, [
                        m("img.mt-0", {
                            src: logoImg,
                            alt: 'Lailaps Logo',
                            height: '72',
                            width: '216'
                        })
                    ])
                ]),
                isAuthenticated ? m(".dropdown.me-5.align-items-center", [
                    m("a.nav-link.dropdown-toggle.text-white", {
                        href: "#",
                        id: "navbarDropdown",
                        role: "button",
                        "data-bs-toggle": "dropdown",
                        "aria-expanded": "false"
                    }, currentUser.name),
                    m("ul.dropdown-menu.dropdown-menu-dark.dropdown-menu-end", {
                        "aria-labelledby": "navbarDropdown"
                    }, [
                        m("li", [
                            m("a.dropdown-item", {
                                href: "#!/profile"
                            }, "Profile"),
                        ]),
                        m("li", [
                            m("a.dropdown-item", {
                                href: "#!/logout"
                            }, "Logout")
                        ])
                    ])
                ]) : m("a.nav-link.text-white.me-5", {
                    href: "#!/login"
                }, "Login")
            ])
        ]);
    }
};

export default Layout;