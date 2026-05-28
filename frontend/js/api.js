const API = window.BACKEND_URL || "http://localhost:8088";

async function apiFetch(path, options = {}) {
    const res = await fetch(API + path, {
        credentials: "include",
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    });
    if (res.status === 401) {
        window.location.href = "/pages/login.html";
        return null;
    }
    if (res.status === 204) return null;
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error(data?.detail || "Error en el servidor");
    return data;
}

const api = {
    login:          (body)          => apiFetch("/api/auth/login",    { method: "POST", body: JSON.stringify(body) }),
    logout:         ()              => apiFetch("/api/auth/logout",   { method: "POST" }),
    getProfile:     ()              => apiFetch("/api/profile/me"),
    updateProfile:  (body)          => apiFetch("/api/profile/me",    { method: "PUT",  body: JSON.stringify(body) }),
    getTrips:       ()              => apiFetch("/api/trips/"),
    getTrip:        (id)            => apiFetch(`/api/trips/${id}`),
    createTrip:     (body)          => apiFetch("/api/trips/",        { method: "POST", body: JSON.stringify(body) }),
    updateTrip:     (id, body)      => apiFetch(`/api/trips/${id}`,   { method: "PUT",  body: JSON.stringify(body) }),
    deleteTrip:     (id)            => apiFetch(`/api/trips/${id}`,   { method: "DELETE" }),
    getUsers:       ()              => apiFetch("/api/admin/users"),
    createUser:     (body)          => apiFetch("/api/admin/users",   { method: "POST", body: JSON.stringify(body) }),
    deleteUser:     (id)            => apiFetch(`/api/admin/users/${id}`, { method: "DELETE" }),
    // Couple
    getCoupleStatus: ()         => apiFetch("/api/couple/status"),
    invite:          (username) => apiFetch("/api/couple/invite", { method: "POST", body: JSON.stringify({ username }) }),
    acceptCouple:    ()         => apiFetch("/api/couple/accept", { method: "POST" }),
    rejectCouple:    ()         => apiFetch("/api/couple/reject", { method: "POST" }),
    cancelCouple:    ()         => apiFetch("/api/couple/cancel", { method: "POST" }),
    unlinkCouple:    ()         => apiFetch("/api/couple/unlink", { method: "POST" }),
    // Places
    getPlaces:      (tripId)        => apiFetch(`/api/trips/${tripId}/places/`),
    createPlace:    (tripId, body)  => apiFetch(`/api/trips/${tripId}/places/`,           { method: "POST",   body: JSON.stringify(body) }),
    updatePlace:    (tripId, plId, body) => apiFetch(`/api/trips/${tripId}/places/${plId}`, { method: "PUT",    body: JSON.stringify(body) }),
    deletePlace:    (tripId, plId)  => apiFetch(`/api/trips/${tripId}/places/${plId}`,    { method: "DELETE" }),
};
