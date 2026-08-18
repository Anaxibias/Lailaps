import m from "mithril";

const userJobs = [{
    jobId: 1,
    jobTitle: "title1",
    company: "company1",
    url: "url1",
    applied: false,
    isArchived: false,
    savedOn: null,
    appliedOn: null,
    },
    {
    jobId: 2,
    jobTitle: "title2",
    company: "company2",
    url: "url2",
    applied: true,
    isArchived: false,
    savedOn: null,
    appliedOn: null
    },
    {
    jobId: 3,
    jobTitle: "title3",
    company: "company3",
    url: "url3",
    applied: true,
    isArchived: true,
    savedOn: null,
    appliedOn: null
    }
];

const Dashboard = {
    view: () => {
        return [
            m("div", { style: { height: "100px" } }),
            m(".container-fluid.px-0", { style: { maxWidth: "1600px", margin: "0 auto" } }, [
                
                // Add Job Form
                // Action: {{ url_for('dashboard') }}
                m("form", { onsubmit: (e) => e.preventDefault(), novalidate: true }, [
                    m(".mb-3", [
                        m("p.mb-1", "Submit a Job URL"),
                        // {{ url_form.url(...) }}
                        m("input.form-control", { id: "url-input", placeholder: "Job URL" })
                    ]),
                    m(".text-center.my-3", "or"),
                    m("p.mb-1", "Enter the job details manually"),
                    m(".row.g-2.mb-3", [
                        // {{ info_form.job_title(...) }}
                        m(".col-md-6", m("input.form-control", { id: "title-input", placeholder: "Job Title" })),
                        // {{ info_form.job_company(...) }}
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
                                userJobs.map((userJob) => {
                                    if (!userJob.isArchived) {
                                        return m(".col-12.job-row", { "data-job-search": `${userJob.jobTitle} ${userJob.company}` }, [
                                            m(".card.job-card.text-white.h-100", [
                                                m(".card-body", [
                                                    m(".row.align-items-center.g-2.saved-job-row", [
                                                        
                                                        // Status Check
                                                        m(".col-md-1.d-flex.justify-content-center.saved-job-status", [
                                                            // Action: {{ url_for('update_status', job_id=row.Job.id) }}
                                                            
                                                            // {% if row.UserJob.application_status.value == 'Applied' %}
                                                            // (Not Applied state rendering goes here)
                                                            
                                                            // {% else %}
                                                            m("button.btn.btn-link.p-0.text-secondary", {
                                                                type: "button",
                                                                title: "Mark as Applied",
                                                                "data-bs-toggle": "tooltip",
                                                                "data-bs-placement": "bottom"
                                                            }, [
                                                                m("i.bi.bi-check-circle", { style: { fontSize: "1.1rem" } })
                                                            ])
                                                            // {% endif %}
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
                                                                // Action: {{ url_for('update_status', job_id=row.Job.id) }}
                                                                
                                                                // {% if row.UserJob.application_status.value != 'Applied' %}
                                                                m("a.badge.rounded-pill.badge-not-applied.badge-custom", { 
                                                                    href: userJob.url, 
                                                                    target: "_blank", 
                                                                    style: { width: "110px", textDecoration: "none" } 
                                                                }, "Apply Now"),
                                                                
                                                                // {% else %}
                                                                // (View Listing state rendering goes here)
                                                                // {% endif %}
                                                                
                                                                m(".d-flex.align-items-center.justify-content-end.saved-job-functions", [
                                                                    // Action: {{ url_for('archive_application', job_id=row.UserJob.id) }}
                                                                    m("button.btn", { type: "button", title: "Archive", style: { backgroundColor: "transparent", border: "none" } }, [
                                                                        m("i.bi.bi-archive.action-icon", { style: { fontSize: "1.25rem" } })
                                                                    ]),
                                                                    // Action: {{ url_for('remove_job', job_id=row.Job.id) }}
                                                                    m("button.btn", { 
                                                                        type: "button", 
                                                                        title: "Delete", 
                                                                        style: { background: "none", border: "none" },
                                                                        "data-bs-toggle": "modal",
                                                                        "data-bs-target": "#confirmDeleteModal{{ row.Job.id }}"
                                                                    }, [
                                                                        m("i.bi.bi-trash.action-icon", { style: { fontSize: "1.25rem" } })
                                                                    ])
                                                                ])
                                                            ])
                                                        ])
                                                    ])
                                                ])
                                            ])
                                        ])}
                                    })
                                ]) : m("p.mb-0", "No job listings saved yet.")                           
                            ])
                ]),
                
                // Archived Section
                m(".mt-4", [
                    m("h2", "Archived"),
                    m(".border.border-light.p-3.rounded", { style: { backgroundColor: "rgba(255, 255, 255, 0.1)" } }, [
                        userJobs.length > 0 ? m(".row.g-3", { id: "archived-jobs-list" }, [
                        // ... identical structure to Saved Jobs but checking {% if row.UserJob.is_archived == True %}
                        // {% else %}
                        ]) : m("p.mb-0", "No archived job listings.")
                    ])
                ])
            ])
        ];
    }
};

export default Dashboard;