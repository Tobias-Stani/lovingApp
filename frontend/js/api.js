const API = "";

async function apiFetch(path, options = {}) {
    const res = await fetch(API + path, {
        credentials: "include",
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
    });
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
    // Todos (por viaje)
    getTodos:       (tripId)               => apiFetch(`/api/trips/${tripId}/todos/`),
    createTodo:     (tripId, body)         => apiFetch(`/api/trips/${tripId}/todos/`,              { method: "POST",   body: JSON.stringify(body) }),
    updateTodo:     (tripId, todoId, body) => apiFetch(`/api/trips/${tripId}/todos/${todoId}`,     { method: "PUT",    body: JSON.stringify(body) }),
    deleteTodo:     (tripId, todoId)       => apiFetch(`/api/trips/${tripId}/todos/${todoId}`,     { method: "DELETE" }),
    // Todos globales
    getGlobalTodos:    ()           => apiFetch("/api/todos/"),
    createGlobalTodo:  (body)       => apiFetch("/api/todos/",          { method: "POST",   body: JSON.stringify(body) }),
    updateGlobalTodo:  (id, body)   => apiFetch(`/api/todos/${id}`,     { method: "PUT",    body: JSON.stringify(body) }),
    deleteGlobalTodo:  (id)         => apiFetch(`/api/todos/${id}`,     { method: "DELETE" }),
    // Dates
    getDates:          ()              => apiFetch("/api/dates/"),
    getDate:           (id)            => apiFetch(`/api/dates/${id}`),
    createDate:        (formData)      => fetch(API + "/api/dates/", { method: "POST", credentials: "include", body: formData }),
    updateDate:        (id, formData)  => fetch(API + `/api/dates/${id}`, { method: "PUT", credentials: "include", body: formData }),
    deleteDate:        (id)            => apiFetch(`/api/dates/${id}`, { method: "DELETE" }),
    addDatePhotos:     (id, formData)  => fetch(API + `/api/dates/${id}/photos`, { method: "POST", credentials: "include", body: formData }),
    deleteDatePhoto:   (photoId)       => apiFetch(`/api/dates/photos/${photoId}`, { method: "DELETE" }),
    // Activity endpoints
    getDateActivities: (dateId)         => apiFetch(`/api/dates/${dateId}/activities`),
    createDateActivity:(dateId, formData) => fetch(API + `/api/dates/${dateId}/activities`, { method: "POST", credentials: "include", body: formData }),
    updateDateActivity:(actId, formData) => fetch(API + `/api/dates/activities/${actId}`, { method: "PUT", credentials: "include", body: formData }),
    deleteDateActivity:(actId)          => apiFetch(`/api/dates/activities/${actId}`, { method: "DELETE" }),
    reorderActivities: (dateId, ids)     => apiFetch(`/api/dates/activities/reorder`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({date_id: dateId, activity_ids: ids}),
    }),
};
