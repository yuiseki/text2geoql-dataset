[out:json][timeout:30000];
area["name:en"="Kobe"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="soba"](area.inner)(area.outer);
);
out geom;
