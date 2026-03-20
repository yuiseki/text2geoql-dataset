[out:json][timeout:30];
area["name:en"="South Sudan"]->.outer;
area["name:en"="Juba"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
