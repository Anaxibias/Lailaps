function toIsoOrNull(value) {
	if (!value) {
		return null;
	}

	const parsed = new Date(value);
	return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

function toBoolean(value, fallback = false) {
	if (typeof value === "boolean") {
		return value;
	}

	if (typeof value === "string") {
		const normalized = value.trim().toLowerCase();
		if (normalized === "true") {
			return true;
		}
		if (normalized === "false") {
			return false;
		}
	}

	return fallback;
}

function toApplicationStatus(raw) {
	const value = raw?.applicationStatus ?? raw?.application_status ?? raw?.status;

	if (typeof value === "string" && value.trim().length > 0) {
		return value;
	}

	const applied = raw?.applied ?? raw?.is_applied;
	return toBoolean(applied, false) ? "Applied" : "Not Applied";
}

export function normalizeUserJob(raw = {}) {
	const fromRow = raw?.Job || raw?.UserJob;
	const job = raw?.Job || raw;
	const userJob = raw?.UserJob || raw;

	const id = raw?.id ?? raw?.jobId ?? raw?.job_id ?? job?.id ?? fromRow?.id ?? null;
	const url = job?.url ?? job?.source ?? raw?.url ?? raw?.source ?? "";
	const jobTitle = job?.jobTitle ?? job?.job_title ?? raw?.jobTitle ?? raw?.job_title ?? raw?.title ?? "";
	const company = job?.company ?? raw?.company ?? raw?.job_company ?? "";
	const savedOn = userJob?.savedOn ?? userJob?.created_at ?? raw?.savedOn ?? raw?.created_at ?? null;
	const appliedOn = userJob?.appliedOn ?? userJob?.applied_on ?? raw?.appliedOn ?? raw?.applied_on ?? null;

	return {
		id,
		jobId: id,
		jobTitle,
		company,
		url,
		isArchived: toBoolean(userJob?.isArchived ?? userJob?.is_archived ?? raw?.isArchived ?? raw?.is_archived, false),
		applicationStatus: toApplicationStatus(raw),
		savedOn: toIsoOrNull(savedOn),
		appliedOn: toIsoOrNull(appliedOn)
	};
}

export function normalizeUserJobs(items) {
	if (!Array.isArray(items)) {
		return [];
	}

	return items.map(normalizeUserJob);
}
