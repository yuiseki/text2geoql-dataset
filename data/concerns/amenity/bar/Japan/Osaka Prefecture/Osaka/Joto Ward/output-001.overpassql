[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Joto Ward"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
