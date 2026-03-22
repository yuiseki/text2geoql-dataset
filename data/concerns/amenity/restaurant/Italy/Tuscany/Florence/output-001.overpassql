[out:json][timeout:30];
area["name:en"="Tuscany"]->.outer;
area["name:en"="Florence"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;