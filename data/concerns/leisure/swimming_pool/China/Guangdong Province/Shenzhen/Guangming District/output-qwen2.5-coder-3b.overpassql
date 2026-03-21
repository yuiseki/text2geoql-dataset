[out:json][timeout:30];
area["name:en"="Guangdong Province"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["leisure"="swimming_pool"](area.inner)(area.outer);
);
out geom;
