[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Futian District"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
