[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["building"~"library"](area.inner)(area.outer);
);
out geom;
