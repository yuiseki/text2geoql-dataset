[out:json][timeout:30];
area["name:en"="Nagoya"][boundary=administrative]->.outer;
area["name:en"="Minato Ward"]->.inner;
(
  nwr["tourism"="picnic_site"](area.inner)(area.outer);
);
out geom;
