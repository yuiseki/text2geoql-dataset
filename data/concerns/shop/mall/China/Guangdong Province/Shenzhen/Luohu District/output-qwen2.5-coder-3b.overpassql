[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
