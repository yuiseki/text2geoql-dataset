[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
