class Dashing.HotStatus extends Dashing.Widget

  constructor: ->
    super

  onData: (data) ->
    return if not @status
    status = @status.toLowerCase()

    if [ 'critical', 'warning', 'ok', 'unknown' ].indexOf(status) != -1
      backgroundClass = "hot-status-#{status}"
    else
      backgroundClass = "hot-status-neutral"

    lastClass = @lastClass

    if lastClass != backgroundClass
      $(@node).toggleClass("#{lastClass} #{backgroundClass}")
      @lastClass = backgroundClass

      audiosound = @get(status + 'sound')
      audioplayer = new Audio(audiosound) if audiosound?
      if audioplayer
        audioplayer.play()

  ready: ->
    @onData(null)
