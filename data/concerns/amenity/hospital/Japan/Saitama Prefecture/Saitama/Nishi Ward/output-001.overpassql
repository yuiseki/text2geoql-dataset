[out:json][timeout:30000];
area["name:en"="Saitama"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
