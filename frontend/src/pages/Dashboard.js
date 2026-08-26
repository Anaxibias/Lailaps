import m from "mithril";
import { requestWithRetry } from "../utils/request";
import { normalizeUserJob, normalizeUserJobs } from "../utils/jobs";

let activeModalType = null; // delete, edit, null
let activeJob = null;
let editDraft = { jobTitle: "", company: "", url: "" };

const userJobs = [];

function openDeleteModal(job) {
    activeModalType = "delete";
    activeJob = job;
    const el = document.getElementById("jobActionModal");
    bootstrap.Modal.getOrCreateInstance(el).show();
}

function openEditModal(job) {
    activeModalType = "edit";
    activeJob = job;
    editDraft = {
        jobTitle: job?.jobTitle || "",
        company: job?.company || "",
        url: job?.url || ""
    };
    const el = document.getElementById("jobActionModal");
    bootstrap.Modal.getOrCreateInstance(el).show();
}

function openModal(type, job) {
    if (type === "edit") {
        openEditModal(job);
        return;
    }

    openDeleteModal(job);
}

function closeModal() {
    const el = document.getElementById("jobActionModal");
    bootstrap.Modal.getInstance(el)?.hide();
    activeModalType = null;
    activeJob = null;
}


const Dashboard = {
    oninit: function(vnode) {
        requestWithRetry("/api/:username/dashboard", {
            method: "GET",
            params: { username: currentUser.name, id: currentUser.id }
        })
        .then(function(result) {
            userJobs.length = 0;
            normalizeUserJobs(result).forEach((job) => userJobs.push(job));
        });
    },
    view: () => {
        return [
            m("div", { style: { height: "100px" } }),
            m(".container-fluid.px-0", { style: { maxWidth: "1600px", margin: "0 auto" } }, [
                
                m("form", { 
                    onsubmit: (e) => {
                        e.preventDefault(); 

                        const url = document.getElementById("url-input").value;
                        const title = document.getElementById("title-input").value;
                        const company = document.getElementById("company-input").value;

                        requestWithRetry("/api/:username/dashboard/add_job", {
                            method: "POST",
                            params: { username: currentUser.name, id: currentUser.id },
                            body: { url, job_title: title, job_company: company }
                        })
                        .then((createdJob) => {
                            userJobs.push(normalizeUserJob(createdJob));
                        })
                        .catch((error) => {
                            console.error("Error adding job:", error);
                        });   
                    },
                    novalidate: true
                }, [m(".mb-3", [
                        m("p.mb-1", "Submit a Job URL"),
                        m("input.form-control", { id: "url-input", placeholder: "Job URL" })
                    ]),
                    m(".text-center.my-3", "or"),
                    m("p.mb-1", "Enter the job details manually"),
                    m(".row.g-2.mb-3", [
                        m(".col-md-6", m("input.form-control", { id: "title-input", placeholder: "Job Title" })),
                        m(".col-md-6", m("input.form-control", { id: "company-input", placeholder: "Company" }))
                    ]),
                    m(".text-center", [
                        m("button.btn.btn-primary", { type: "submit", style: { width: "150px" } }, "Save Job")
                    ])
                ]),

                // Saved Jobs Section
                m(".mt-4", [
                    m(".d-flex.justify-content-between.align-items-center.mb-3", [
                        m("h2.mb-0", "Saved Jobs"),
                        m("div", { style: { width: "220px", maxWidth: "100%" } }, [
                            m("input.form-control.form-control-sm", { 
                                type: "text", 
                                id: "saved-job-filter", 
                                placeholder: "Filter jobs", 
                                "aria-label": "Filter saved jobs" 
                            })
                        ])
                    ]),
                    m(".border.border-light.p-3.rounded", { style: { backgroundColor: "rgba(255, 255, 255, 0.1)" } }, [
                        
                        userJobs.length > 0 ? m(".row.g-3", { id: "saved-jobs-list" }, [
                                userJobs.filter((userJob) => !userJob.isArchived).map((userJob) => {
                                    return m(".col-12.job-row", { "data-job-search": `${userJob.jobTitle} ${userJob.company}` }, [
                                            m(".card.job-card.text-white.h-100", [
                                                m(".card-body", [
                                                    m(".row.align-items-center.g-2.saved-job-row", [
                                                        
                                                        // Status Check
                                                        m(".col-md-1.d-flex.justify-content-center.saved-job-status", [
                                                            m("form", {
                                                                onsubmit: (e) => {
                                                                    e.preventDefault();
                                                                    
                                                                    requestWithRetry(`/api/:username/dashboard/update_status/${userJob.id}`, {
                                                                        method: "PUT",
                                                                        params: { username: currentUser.name, id: currentUser.id },
                                                                        body: { status: userJob.applicationStatus === "Applied" ? "Not Applied" : "Applied" }
                                                                    })
                                                                    .then(() => {
                                                                        userJob.applicationStatus = userJob.applicationStatus === "Applied" ? "Not Applied" : "Applied";
                                                                    })
                                                                    .catch((error) => {
                                                                        console.error("Error updating status:", error);
                                                                    });
                                                                }
                                                            }, [
                                                                m("button.btn.btn-link.p-0.text-secondary[data-bs-placement='bottom'][data-bs-toggle='tooltip'][title='Mark as Not Applied'][type='submit']", [
                                                                    m("i.bi.bi-check-circle", {style: {"font-size": " 1.1rem"}})
                                                                ])
                                                            ])
                                                        ]),
                                                        
                                                        // Main Info
                                                        m(".col-md-5.text-start.saved-job-main", [
                                                            m("a.job-title-link", { href: userJob.url, target: "_blank", style: { fontSize: "1.05rem" } }, userJob.jobTitle),
                                                            m(".card-text.mt-1", { style: { fontSize: "0.85rem", color: "rgba(219, 219, 219, 0.8)" } }, userJob.company)
                                                        ]),
                                                        
                                                        // Date
                                                        m(".col-md-3.text-start.saved-job-date", [
                                                            m(".card-text.mb-0", { style: { fontSize: "0.8rem", color: "rgba(219, 219, 219, 0.7)" } }, userJob.savedOn ? `Saved on: ${new Date(userJob.savedOn).toLocaleDateString()}` : "Saved on: N/A")
                                                        ]),
                                                        
                                                        // Action Buttons
                                                        m(".col-md-3.d-flex.justify-content-md-end.justify-content-start.saved-job-action", [
                                                            m(".saved-job-bottom-row", [
                                                                (userJob.applicationStatus !== "Applied") ? m("a.badge.rounded-pill.badge-not-applied.badge-custom", { 
                                                                    href: userJob.url, 
                                                                    target: "_blank", 
                                                                    style: { width: "110px", textDecoration: "none" } 
                                                                }, "Apply Now") : m("a.badge.rounded-pill.badge-applied.badge-custom", { 
                                                                    href: userJob.url, 
                                                                    target: "_blank", 
                                                                    style: { width: "110px", textDecoration: "none" } 
                                                                }, "View Listing"),                                       
                                                                
                                                                m(".d-flex.align-items-center.justify-content-end.saved-job-functions", [
                                                                    m("form", {
                                                                        onsubmit: (e) => {
                                                                            e.preventDefault();
                                                                            requestWithRetry(`/api/:username/dashboard/archive/${userJob.id}`, {
                                                                                method: "PUT",
                                                                                params: { username: currentUser.name, id: currentUser.id },
                                                                                body: { is_archived: true }
                                                                            })
                                                                            .then(() => {
                                                                                userJob.isArchived = true;
                                                                            })
                                                                            .catch((error) => {
                                                                                console.error("Error archiving job:", error);
                                                                            });
                                                                        }
                                                                    }, [
                                                                        m("button.btn", { type: "button", title: "Archive", style: { backgroundColor: "transparent", border: "none" } }, [
                                                                            m("i.bi.bi-archive.action-icon", { style: { fontSize: "1.25rem" } })
                                                                        ])
                                                                    ]),
                                                                    // Action: {{ url_for('remove_job', job_id=row.Job.id) }}
                                                                    m("form", {
                                                                        onsubmit: (e) => {
                                                                            e.preventDefault();
                                                                            requestWithRetry(`/api/:username/dashboard/remove_job/${userJob.id}`, {
                                                                                method: "DELETE",
                                                                                params: { username: currentUser.name, id: currentUser.id }
                                                                            })
                                                                            .then(() => {
                                                                                const index = userJobs.findIndex(job => job.id === userJob.id);
                                                                                if (index !== -1) {
                                                                                    userJobs.splice(index, 1);
                                                                                }
                                                                            })
                                                                            .catch((error) => {
                                                                                console.error("Error deleting job:", error);
                                                                            });
                                                                        }
                                                                    }, [
                                                                    m("button.btn", { 
                                                                        type: "button", 
                                                                        title: "Delete", 
                                                                        style: { background: "none", border: "none" },
                                                                        onclick: () => openModal("delete", userJob)
                                                                    }, [
                                                                        m("i.bi.bi-trash.action-icon", { style: { fontSize: "1.25rem" } })
                                                                    ])
                                                                ])
                                                            ])
                                                        ])
                                                    ])
                                                ])
                                            ])
                                        ])
                                        ]);
                                    })
                                ]) : m("p.mb-0", "No job listings saved yet.")                           
                            ])
                ]),
                
                // Archived Section
                m(".mt-4", [
                    m("h2", "Archived"),
                    m(".border.border-light.p-3.rounded", { style: { backgroundColor: "rgba(255, 255, 255, 0.1)" } }, [
                        userJobs.length > 0 ? m(".row.g-3", { id: "archived-jobs-list" }, [
                            userJobs.filter((userJob) => userJob.isArchived).map((userJob) => {
                                return m(".col-12.job-row", { "data-job-search": `${userJob.jobTitle} ${userJob.company}` }, [
                                    m(".card.job-card.text-white.h-100", [
                                        m(".card-body", [
                                            m(".row.align-items-center.g-2.saved-job-row", [
                                                m(".col-md-1.d-flex.justify-content-center.saved-job-status", [
                                                    m("form", {
                                                        onsubmit: (e) => {
                                                            e.preventDefault();
                                                            requestWithRetry(`/api/:username/dashboard/update_status/${userJob.id}`, {
                                                                method: "PUT",
                                                                params: { username: currentUser.name, id: currentUser.id },
                                                                body: { status: userJob.applicationStatus === "Applied" ? "Not Applied" : "Applied" }
                                                            })
                                                            .then(() => {
                                                                userJob.applicationStatus = userJob.applicationStatus === "Applied" ? "Not Applied" : "Applied";
                                                            })
                                                            .catch((error) => {
                                                                console.error("Error updating status:", error);
                                                            });
                                                        }
                                                    }, [
                                                        m("button.btn.btn-link.p-0.text-secondary[data-bs-placement='bottom'][data-bs-toggle='tooltip'][title='Mark as Not Applied'][type='submit']", [
                                                            m("i.bi.bi-check-circle", {style: {"font-size": " 1.1rem"}})
                                                        ])
                                                    ])
                                                ]),

                                                m(".col-md-5.text-start.saved-job-main", [
                                                    m("a.job-title-link", { href: userJob.url, target: "_blank", style: { fontSize: "1.05rem" } }, userJob.jobTitle),
                                                    m(".card-text.mt-1", { style: { fontSize: "0.85rem", color: "rgba(219, 219, 219, 0.8)" } }, userJob.company)
                                                ]),

                                                m(".col-md-3.text-start.saved-job-date", [
                                                    m(".card-text.mb-0", { style: { fontSize: "0.8rem", color: "rgba(219, 219, 219, 0.7)" } }, userJob.savedOn ? `Saved on: ${new Date(userJob.savedOn).toLocaleDateString()}` : "Saved on: N/A")
                                                ]),

                                                m(".col-md-3.d-flex.justify-content-md-end.justify-content-start.saved-job-action", [
                                                    m(".saved-job-bottom-row", [
                                                        m("form", {
                                                            onsubmit: (e) => {
                                                                e.preventDefault();
                                                                requestWithRetry(`/api/:username/dashboard/update_status/${userJob.id}`, {
                                                                    method: "PUT",
                                                                    params: { username: currentUser.name, id: currentUser.id },
                                                                    body: { status: "Not Applied" }
                                                                })
                                                                .then(() => {
                                                                    userJob.applicationStatus = "Not Applied";
                                                                })
                                                                .catch((error) => {
                                                                    console.error("Error updating status:", error);
                                                                });
                                                            }
                                                        }, [
                                                            m("button.badge.rounded-pill.badge-archived.badge-custom", { type: "submit", style: { width: "110px", border: "none" } }, "Archived")
                                                        ]),

                                                        m(".d-flex.align-items-center.justify-content-end.saved-job-functions", [
                                                            m("form", {
                                                                onsubmit: (e) => {
                                                                    e.preventDefault();
                                                                    requestWithRetry(`/api/:username/dashboard/archive/${userJob.id}`, {
                                                                        method: "PUT",
                                                                        params: { username: currentUser.name, id: currentUser.id },
                                                                        body: { is_archived: false }
                                                                    })
                                                                    .then(() => {
                                                                        userJob.isArchived = false;
                                                                    })
                                                                    .catch((error) => {
                                                                        console.error("Error unarchiving job:", error);
                                                                    });
                                                                }
                                                            }, [
                                                                m("button.btn", { type: "button", title: "Unarchive", style: { backgroundColor: "transparent", border: "none" } }, [
                                                                    m("i.bi.bi-archive.action-icon", { style: { fontSize: "1.25rem" } })
                                                                ])
                                                            ]),
                                                            m("form", {
                                                                onsubmit: (e) => {
                                                                    e.preventDefault();
                                                                    requestWithRetry(`/api/:username/dashboard/remove_job/${userJob.id}`, {
                                                                        method: "DELETE",
                                                                        params: { username: currentUser.name, id: currentUser.id }
                                                                    })
                                                                    .then(() => {
                                                                        const index = userJobs.findIndex(job => job.id === userJob.id);
                                                                        if (index !== -1) {
                                                                            userJobs.splice(index, 1);
                                                                        }
                                                                    })
                                                                    .catch((error) => {
                                                                        console.error("Error deleting job:", error);
                                                                    });
                                                                }
                                                            }, [
                                                                m("button.btn", {
                                                                    type: "button",
                                                                    title: "Delete",
                                                                    style: { background: "none", border: "none" },
                                                                    onclick: () => openModal("delete", userJob)
                                                                }, [
                                                                    m("i.bi.bi-trash.action-icon", { style: { fontSize: "1.25rem" } })
                                                                ])
                                                            ])
                                                        ])
                                                    ])
                                                ])
                                            ])
                                        ])
                                    ])
                                ]);
                            })
                        ]) : m("p.mb-0", "No archived job listings.")
                    ])
                ])
            ]),

            m(".modal.fade", {
                id: "jobActionModal",
                tabindex: "-1",
                "aria-hidden": "true"
            }, [
                m(".modal-dialog", [
                    m(".modal-content.bg-dark.text-white", [
                        m(".modal-header", [
                            m("h5.modal-title", activeModalType === "edit" ? "Edit Job" : "Confirm Deletion"),
                            m("button.btn-close.btn-close-white", {
                                type: "button",
                                "data-bs-dismiss": "modal",
                                "aria-label": "Close",
                                onclick: closeModal
                            })
                        ]),
                        m(".modal-body", [
                            activeModalType === "edit"
                                ? m(".d-grid.gap-2", [
                                    m("input.form-control", {
                                        placeholder: "Job Title",
                                        value: editDraft.jobTitle,
                                        oninput: (e) => {
                                            editDraft.jobTitle = e.target.value;
                                        }
                                    }),
                                    m("input.form-control", {
                                        placeholder: "Company",
                                        value: editDraft.company,
                                        oninput: (e) => {
                                            editDraft.company = e.target.value;
                                        }
                                    }),
                                    m("input.form-control", {
                                        placeholder: "Job URL",
                                        value: editDraft.url,
                                        oninput: (e) => {
                                            editDraft.url = e.target.value;
                                        }
                                    })
                                ])
                                : `Are you sure you want to delete ${activeJob?.jobTitle || "this job"}?`
                        ]),
                        m(".modal-footer", [
                            m("button.btn.btn-secondary", {
                                type: "button",
                                "data-bs-dismiss": "modal",
                                onclick: closeModal
                            }, "Cancel"),
                            activeModalType === "edit"
                                ? m("button.btn.btn-primary", {
                                    type: "button",
                                    onclick: () => {
                                        if (!activeJob) {
                                            return;
                                        }

                                        activeJob.jobTitle = editDraft.jobTitle;
                                        activeJob.company = editDraft.company;
                                        activeJob.url = editDraft.url;
                                        
                                        requestWithRetry(`/api/:username/dashboard/update_job/${activeJob.id}`, {
                                            method: "PUT",
                                            params: { id: currentUser.id} ,
                                            body: {
                                                job_title: activeJob.jobTitle,
                                                job_company: activeJob.company,
                                                url: activeJob.url
                                            }
                                        })
                                        .then(() => {
                                            closeModal();
                                            m.redraw();
                                        });
                                    }
                                }, "Save")
                                : m("button.btn.btn-danger", {
                                    type: "button",
                                    onclick: () => {
                                        if (!activeJob) {
                                            return;
                                        }

                                        requestWithRetry(`/api/:username/dashboard/remove_job/${activeJob.id}`, {
                                            method: "DELETE",
                                            params: { username: currentUser.name, id: currentUser.id }
                                        })
                                        .then(() => {
                                            const index = userJobs.findIndex((job) => job.id === activeJob.id);
                                            if (index !== -1) {
                                                userJobs.splice(index, 1);
                                            }

                                            closeModal();
                                            m.redraw();
                                        })
                                        .catch((error) => {
                                            console.error("Error deleting job:", error);
                                        });
                                    }
                                }, "Delete")
                        ])
                    ])
                ])
            ])
        ];
    }
};

export default Dashboard;