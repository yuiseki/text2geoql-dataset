[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["historic"~"ruins"](area.inner)(area.outer);
);
out geom;
