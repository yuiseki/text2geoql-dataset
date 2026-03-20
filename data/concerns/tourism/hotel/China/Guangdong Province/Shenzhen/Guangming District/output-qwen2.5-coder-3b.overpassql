[out:json][timeout:30];
area["name:zh"="光明区"]->.outer;
area["name:en"="Guangming District"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;
