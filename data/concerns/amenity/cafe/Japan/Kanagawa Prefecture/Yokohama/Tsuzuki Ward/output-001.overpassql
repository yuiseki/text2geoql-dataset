[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Tsuzuki Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
