[out:json][timeout:30];
area["name:ja"="高知県"][boundary=administrative]->.outer;
area["name:ja"="高知県"][boundary=administrative]->.inner;
(
  nwr["tourism"="picnic_site"](area.inner)(area.outer);
);
out geom;
