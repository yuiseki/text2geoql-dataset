[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Midori Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
