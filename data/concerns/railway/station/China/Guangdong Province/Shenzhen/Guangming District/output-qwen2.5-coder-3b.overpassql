[out:json][timeout:30];
area["name:zh"="光明区"]->.outer;
area["name:en"="Guangming District"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
