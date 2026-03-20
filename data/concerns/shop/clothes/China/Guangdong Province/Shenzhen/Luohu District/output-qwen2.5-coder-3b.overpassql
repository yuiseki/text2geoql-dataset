[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["shop"~"clothes"](area.inner)(area.outer);
);
out geom;
