[out:json][timeout:30];
area["name:en"="Guangming District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["historic"~"ruins"](area.inner)(area.outer);
);
out geom;
