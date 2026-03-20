[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
