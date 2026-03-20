[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Midori Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
