[out:json][timeout:30];
area["name:en"="Valencian Community"]->.outer;
area["name:en"="Valencia"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;