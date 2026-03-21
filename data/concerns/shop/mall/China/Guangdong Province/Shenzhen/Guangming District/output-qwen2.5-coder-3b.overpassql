[out:json][timeout:30];
area["name:en"="Guangming District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
