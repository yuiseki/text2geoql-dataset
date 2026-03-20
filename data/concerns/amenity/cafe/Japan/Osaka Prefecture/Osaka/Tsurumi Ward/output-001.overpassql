[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Tsurumi Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
