[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["amenity"~"bank"](area.inner)(area.outer);
);
out geom;
