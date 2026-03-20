[out:json][timeout:30];
area["name:en"="Pingshan District"][boundary=administrative]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["tourism"="picnic_site"](area.inner)(area.outer);
);
out geom;
