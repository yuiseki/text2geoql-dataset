[out:json][timeout:30];
area["name:zh"="深圳市"][boundary=administrative]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
