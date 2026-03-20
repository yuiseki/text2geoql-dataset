[out:json][timeout:30];
area["name:zh"="深圳市"]->.outer;
area["name:zh"="南山区"]->.inner;
(
  nwr["tourism"="zoo"](area.inner)(area.outer);
);
out geom;
