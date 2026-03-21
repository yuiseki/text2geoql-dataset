[out:json][timeout:30];
area["name:en"="Guangming District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["amenity"~"police"](area.inner)(area.outer);
);
out geom;
