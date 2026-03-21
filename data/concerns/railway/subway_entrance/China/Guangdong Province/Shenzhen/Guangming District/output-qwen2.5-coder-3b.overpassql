[out:json][timeout:30];
area["name:en"="Guangming District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["railway"~"subway"](area.inner)(area.outer);
);
out geom;
