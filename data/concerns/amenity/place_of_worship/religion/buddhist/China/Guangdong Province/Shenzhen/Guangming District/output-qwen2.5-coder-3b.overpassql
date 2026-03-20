[out:json][timeout:30];
area["name:zh"="光明区"]->.outer;
area["name:en"="Guangming District"]->.inner;
(
  nwr["building"~"temple"](area.inner)(area.outer);
);
out geom;
