[out:json][timeout:30];
area["name:en"="Shenzhen"][boundary=administrative]->.outer;
area["name:zh"="深圳市"][boundary=administrative]->.inner;
(
  nwr["shop"~"supermarket"](area.inner)(area.outer);
);
out geom;
