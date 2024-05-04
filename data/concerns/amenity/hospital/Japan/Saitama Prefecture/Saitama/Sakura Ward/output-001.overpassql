[out:json][timeout:30000];
area["name:en"="Sakura Ward"]->.outer;
area["name:en"="Saitama"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
